import { useState, useEffect } from 'react';
import { FaStar, FaRegStar } from 'react-icons/fa';
import { ratingService } from '@/services';

interface MovieRatingProps {
    movieId: number;
    averageRating: number | null;
    userRating?: number | null;
    onRatingChange?: () => void;
}

export const MovieRating = ({
    movieId,
    averageRating,
    userRating: initialUserRating,
    onRatingChange
}: MovieRatingProps) => {
    const [userRating, setUserRating] = useState<number | null>(initialUserRating || null);
    const [hoverRating, setHoverRating] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Update local state when prop changes (after refetch)
    useEffect(() => {
        setUserRating(initialUserRating || null);
    }, [initialUserRating]);

    const handleRate = async (score: number) => {
        console.log('=== RATING DEBUG ===');
        console.log('Attempting to rate movie:', movieId, 'with score:', score);

        if (isLoading) {
            console.log('Already loading, skipping...');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            console.log('Calling ratingService.rateMovie...');
            const result = await ratingService.rateMovie({ movie: movieId, score });
            console.log('Rating saved successfully:', result);

            setUserRating(score);

            // Notify parent component to refresh data
            if (onRatingChange) {
                console.log('Calling onRatingChange to refresh data...');
                onRatingChange();
            }

            console.log('Rating process completed!');
        } catch (err: any) {
            console.error('Failed to rate movie:', err);
            console.error('Error details:', err.response?.data || err.message);
            setError(err.response?.data?.detail || err.message || 'Failed to rate movie');
        } finally {
            setIsLoading(false);
            console.log('=== END RATING DEBUG ===');
        }
    };

    const displayRating = hoverRating || userRating || 0;

    return (
        <div className="flex flex-col gap-3">
            {/* Average Rating Display */}
            <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Average Rating:</span>
                <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <FaStar
                            key={`avg-${star}`}
                            className={`text-lg ${star <= Math.round(averageRating || 0)
                                ? 'text-yellow-400'
                                : 'text-gray-300'
                                }`}
                        />
                    ))}
                    <span className="ml-2 text-sm text-gray-600 font-medium">
                        {averageRating ? averageRating.toFixed(1) : 'N/A'}
                    </span>
                </div>
            </div>

            {/* User Rating Input */}
            <div className="flex flex-col gap-2">
                <span className="text-sm font-medium text-gray-700">Your Rating:</span>
                <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <button
                            key={`user-${star}`}
                            type="button"
                            onClick={() => {
                                console.log('Star clicked:', star);
                                handleRate(star);
                            }}
                            onMouseEnter={() => setHoverRating(star)}
                            onMouseLeave={() => setHoverRating(0)}
                            disabled={isLoading}
                            className="transition-transform hover:scale-125 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {star <= displayRating ? (
                                <FaStar className="text-2xl text-yellow-400" />
                            ) : (
                                <FaRegStar className="text-2xl text-gray-300" />
                            )}
                        </button>
                    ))}
                    {userRating && (
                        <span className="ml-2 text-sm text-gray-600 font-medium">
                            {userRating}/5
                        </span>
                    )}
                </div>
                {error && (
                    <div className="text-red-500 text-sm">{error}</div>
                )}
                {isLoading && (
                    <div className="text-gray-500 text-sm">Saving rating...</div>
                )}
            </div>
        </div>
    );
};
